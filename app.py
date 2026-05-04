import os
import uuid
import ipaddress
import tempfile
import threading
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_file, render_template
from resume_modifier import (
    convert_pdf_to_markdown,
    get_jd,
    adapt_markdown,
    convert_markdown_to_html,
    convert_html_to_pdf,
)

app = Flask(__name__)
jobs = {}


def _validate_job_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Invalid URL")
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Job URL must use http or https")
    hostname = (parsed.hostname or '').lower()
    if not hostname:
        raise ValueError("Invalid URL: missing host")
    if hostname in ('localhost', '0.0.0.0'):
        raise ValueError("Job URL cannot point to a local address")
    try:
        if ipaddress.ip_address(hostname).is_private or ipaddress.ip_address(hostname).is_loopback:
            raise ValueError("Job URL cannot point to a private or internal address")
    except ValueError as e:
        if 'cannot' in str(e):
            raise
        # hostname is a domain name, not an IP — allowed


def run_pipeline(job_id, tmp_input_path, job_url):
    _, tmp_output_path = tempfile.mkstemp(suffix='.pdf')
    try:
        jobs[job_id]['step'] = 'Converting PDF...'
        markdown = convert_pdf_to_markdown(tmp_input_path)

        jobs[job_id]['step'] = 'Fetching job description...'
        jd = get_jd(job_url)

        jobs[job_id]['step'] = 'Adapting resume...'
        adapted_markdown = adapt_markdown(markdown, jd)

        jobs[job_id]['step'] = 'Generating HTML...'
        html = convert_markdown_to_html(adapted_markdown)

        jobs[job_id]['step'] = 'Rendering PDF...'
        convert_html_to_pdf(html, tmp_output_path)

        jobs[job_id] = {'status': 'done', 'file': tmp_output_path}
    except Exception as e:
        if os.path.exists(tmp_output_path):
            os.unlink(tmp_output_path)
        jobs[job_id] = {'status': 'error', 'message': str(e)}
    finally:
        if os.path.exists(tmp_input_path):
            os.unlink(tmp_input_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('resume')
    job_url = request.form.get('job_url')

    if not file or not job_url:
        return jsonify({'error': 'Resume file and job URL are required'}), 400

    try:
        _validate_job_url(job_url)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    fd, tmp_input_path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    file.save(tmp_input_path)

    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'processing', 'step': 'Starting...'}

    thread = threading.Thread(target=run_pipeline, args=(job_id, tmp_input_path, job_url))
    thread.daemon = True
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/status/<job_id>')
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/download/<job_id>')
def download(job_id):
    job = jobs.get(job_id)
    if not job or job.get('status') != 'done':
        return jsonify({'error': 'File not ready'}), 404
    return send_file(job['file'], as_attachment=True, download_name='adapted_resume.pdf')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

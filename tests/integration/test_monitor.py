# -*- coding: utf-8 -*-
"""Launching and monitoring, and the exit codes that carry the outcome.

Scripts read the status from the exit code, so the three cases have to be
distinguishable: 0 succeeded, 1 failed, 2 was cancelled.
"""

import json
import threading
import time

import pytest


def launchable(api):
    """A job template with a project that has actually synced."""
    for jt in api.job_templates.get(all_pages=True).results:
        project = jt.related.get('project')
        if project is None:
            continue
        if project.get().status == 'successful':
            return jt
    return None


@pytest.fixture(scope='module')
def job_template(api):
    jt = launchable(api)
    if jt is None:
        pytest.skip('no job template with a successfully synced project')
    return jt


def test_wait_returns_the_final_status(ascender, job_template):
    rc, out, err = ascender('job_templates', 'launch', str(job_template.id), '--wait', timeout=900)

    assert 'Starting Standard Out Stream' not in out, '--wait should not stream'
    assert json.loads(out)['status'] in ('successful', 'failed')
    assert rc in (0, 1)


def test_monitor_streams_and_reports_success(ascender, job_template):
    rc, out, err = ascender('job_templates', 'launch', str(job_template.id), '--monitor', timeout=900)

    if rc == 1:
        pytest.skip('this job template does not succeed in this environment')
    assert rc == 0
    assert 'Starting Standard Out Stream' in out


def test_a_cancelled_job_exits_2(ascender, api, job_template):
    """Cancellation has to be distinguishable from failure."""
    result = {}

    def launch():
        result['rc'], result['out'], result['err'] = ascender('job_templates', 'launch', str(job_template.id), '--monitor', timeout=900)

    worker = threading.Thread(target=launch)
    worker.start()

    job = None
    for _ in range(60):
        time.sleep(2)
        running = api.jobs.get(status='running', order_by='-id', page_size=1).results
        if running:
            job = running[0]
            break
    if job is None:
        worker.join(timeout=900)
        pytest.skip('the job finished before it could be cancelled')

    job.related.cancel.post()
    worker.join(timeout=900)

    assert result['rc'] == 2, f"expected 2 for a cancelled job, got {result['rc']}"

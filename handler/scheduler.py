from datetime import datetime
from handler.base import BaseHandler
from app import scheduler
from settings import JOB_IDS


# 要执行的定时任务在这里
def task1(options):
    print('{} [APScheduler][Task]-{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), options))


class SchedulerMainHandler(BaseHandler):
    # 定时任务测试
    def get(self):
        self.write('<a href="/scheduler?job_id=1&action=add">add '
                   'job</a><br><a href="/scheduler?job_id=1&action=remove">remove job</a>')


class SchedulerHandler(BaseHandler):
    def get(self):
        job_id = self.get_query_argument('job_id', None)
        action = self.get_query_argument('action', None)
        if job_id:
            # add
            if 'add' == action:
                if job_id not in JOB_IDS:
                    JOB_IDS.append(job_id)
                    scheduler.add_job(task1, 'interval', seconds=3, id=job_id, args=(job_id,))
                    self.write('[TASK ADDED] - {}'.format(job_id))
                else:
                    self.write('[TASK EXISTS] - {}'.format(job_id))
            # remove
            elif 'remove' == action:
                if job_id in JOB_IDS:
                    scheduler.remove_job(job_id)
                    JOB_IDS.remove(job_id)
                    self.write('[TASK REMOVED] - {}'.format(job_id))
                else:
                    self.write('[TASK NOT FOUND] - {}'.format(job_id))
        else:
            self.write('[INVALID PARAMS] INVALID job_id or action')
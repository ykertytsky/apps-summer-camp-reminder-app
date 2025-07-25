class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.tasks = {}
    def add_task(self, task,time,deadline=None):
        if time in self.tasks:
            self.tasks[time].append((task,deadline))
        else:
            self.tasks[time] = [(task,deadline)]
    def get_all_tasks(self):
        return self.tasks.values()
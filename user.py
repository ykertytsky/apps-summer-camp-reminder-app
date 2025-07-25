class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.reminders = {}
    
    def __str__(self):
        """Return a string representation of the User"""
        return f"User {self.user_id}: {self.reminders}"
    
    def add_task(self, task,time,deadline=None):
        if time in self.reminders:
            self.reminders[time].append((task,deadline))
        else:
            self.reminders[time] = [(task,deadline)]

    def get_tasks(self):
        return self.reminders
    def get_all_tasks(self):
        return self.reminders.values()
import random


class MantisBrain:
    def __init__(self, body):
        self.body = body
        self.state = 'idle'
        self.target = None
        self.damage = 0.01
        self.radius = 5

    def handle_event(self, message, details):

        if self.state is 'idle':

            if message == 'timer':
                world = self.body.world
                x, y = random.random() * world.width, random.random() * world.height
                self.body.go_to((x, y))
                self.body.set_alarm(random.random() * 10)

            elif message == 'collide' and details['what'] == 'Slug':
                self.state = 'curious'
                self.body.set_alarm(1)
                self.body.stop()
                self.target = details['who']

        elif self.state == 'curious':

            if message == 'timer':

                if self.target:
                    if random.random() < 0.5:
                        self.body.stop()
                        self.state = 'idle'

                    else:
                        self.body.go_to(self.target)
                    self.body.set_alarm(1)

            elif message is 'collide' and details['what'] is 'Slug':
                slug = details['who']
                slug.amount -= self.damage  # take a tiny little bite
                self.radius += 0.1
                self.damage += 0.001


class SlugBrain:
    def __init__(self, body):
        self.body = body
        self.state = 'idle'
        self.prev_state = self.state
        self.target = None
        self.no_target = False
        self.has_resource = False
        self.body.set_alarm(0.5)

    def handle_event(self, message, details):

        you = self.body.find_nearest('Slug')

        if you.amount < 0.5:
            self.set_state('flee')

        if message is 'order':
            if details is 'a':
                self.set_state('attack')

            elif details is 'b':
                self.set_state('build')

            elif details is 'd':
                self.body.amount -= 0.75
                print 'ouch!'

            elif details is 'h':
                self.set_state('harvest')

            elif details is 'i':
                self.set_state('idle')

            elif details is 'x':
                self.set_state('bloodlust')
                print 'FOR GLORY!'

            else:
                self.set_state('moving')
                self.body.go_to(details)

        if self.state is 'attack':
            if message is 'timer':
                try:
                    self.target = self.body.find_nearest('Mantis')
                    self.reset_timer()

                except ZeroDivisionError:
                    self.state = 'bloodlust'
                    pass

                except ValueError:
                    self.state = 'bloodlust'
                    pass

            if self.target:
                self.body.go_to(self.target)

            elif self.no_target:
                self.state_finished()

        if self.state is 'build':

            if message is 'collide' and details['what'] is 'Nest':
                nest = details['who']

                if nest.amount < 1:
                    nest.amount += 0.01
                    self.has_resource = False

                else:
                    self.set_state('idle')

            if message is 'timer':
                self.target = self.body.find_nearest('Nest')
                self.reset_timer()

                if self.target:
                    self.body.go_to(self.target)

                elif self.no_target:
                    self.state_finished()

        if self.state is 'harvest':

            if message is 'timer':
                self.target = self.body.find_nearest('Resource')
                self.reset_timer()

            if self.target:
                self.body.go_to(self.target)

            elif self.has_resource:
                self.state_finished()

            elif self.no_target:
                self.state_finished()

            if message is 'collide':

                if details['what'] is 'Resource':
                    resource = details['who']

                    if self.has_resource is True:
                        self.set_state('build')

                    if self.has_resource is False:
                        self.has_resource = True
                        resource.amount -= 0.25

        if self.state is 'idle':
            self.body.stop()

            if message is 'timer':
                self.reset_timer()

        if self.state is 'moving' and message is 'timer':
            self.reset_timer()

        if message is 'collide' and details['what'] is 'Mantis':
            mantis = details['who']
            mantis.amount -= 0.05
            if self.state is not 'attack:':
                self.set_state('attack')

        if self.state is 'flee':
            self.target = self.body.find_nearest('Nest')

            if message is 'timer':
                self.reset_timer()

            self.body.go_to(self.target)

            if message is 'collide' and details['what'] is 'Nest':
                you.amount += 0.5

            if you.amount > 0.75:
                self.state = self.prev_state

        if self.state is 'bloodlust':
            self.target = self.body.find_nearest('Slug')

            if self.target:
                self.body.go_to(self.target)

            elif self.no_target:
                self.state_finished()

            if message is 'collide' and details['what'] is 'Slug':
                slug = details['who']
                slug.amount -= 0.02  # dine upon the flesh of thy comrades

    def reset_timer(self):
        self.body.set_alarm(0.5)

        if self.target:
            self.no_target = False
        else:
            self.no_target = True

    def set_state(self, state):
        if self.prev_state is not self.state:
            self.prev_state = self.state
        self.state = state

    def state_finished(self):
        self.no_target = False
        if self.state == self.prev_state:
            self.state = 'idle'
        else:
            self.state = self.prev_state


world_specification = {
    'worldgen_seed': 4,
    'nests': 2,
    'obstacles': 20,
    'resources': 5,
    'slugs': 5,
    'mantises': 5,
}

brain_classes = {
    'mantis': MantisBrain,
    'slug': SlugBrain,
}
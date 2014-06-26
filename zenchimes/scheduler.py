from multiprocessing import Process
from datetime import date, datetime, time, timedelta
from pytz import timezone
import ConfigParser
import pytz
import os
import signal
import sys
from time import sleep
import logging
from zenchimes.client import LMSCommandLineInterface
from zenchimes.utilities import logged_class
from zenchimes import settings


@logged_class
class ChimeScheduler(Process):
    fmt = '%H:%M:%S'

    def __init__(self, *args, **kwargs):
        """
        Initialize chime scheduler.
        """
        super(ChimeScheduler, self).__init__(target=self.loop, *args, **kwargs)

        # SIGUSR1 to reread configuration and re-initialize schedule.
        signal.signal(signal.SIGUSR1, self.sigusr1_handler)

        self.config = ConfigParser.ConfigParser()
        self.configure()

    def configure(self):
        self.logger.info("Reading configuration.")
        config = self.config
        config.read(settings.CONFIG_FILE)
        self.TIMEZONE = config.get('scheduler', 'timezone')
        self.STARTTIME = config.get('scheduler', 'starttime')
        self.ENDTIME = config.get('scheduler', 'endtime')
        self.CHIME_INTERVAL = int(config.get('scheduler', 'chime_interval'))

        os.environ['TZ'] = self.TIMEZONE
        s = datetime.strptime(self.STARTTIME, self.fmt)
        e = datetime.strptime(self.ENDTIME, self.fmt)

        diff = e - s
        self.event_count = \
                int(diff.total_seconds() / self.CHIME_INTERVAL)
        self.current_event = 0
        self.events = []
        for i in range(self.event_count + 1):
            next_event = \
                s + timedelta(seconds=self.CHIME_INTERVAL * i)
            self.events.append(next_event.time())

        self.startx = time(s.hour, s.minute, s.second)
        self.endx = time(e.hour, e.minute, e.second)

        self.advance_counter()

    def sigusr1_handler(self, signum, frame):
        # Rebuild schedule.
        self.configure()

    def current_time(self):
        t = datetime.now()
        self.logger.debug("current_time: {0}".format(time(t.hour, t.minute, t.second)))
        return time(t.hour, t.minute, t.second)

    def is_event(self):
        current_time = self.current_time()
        current_event_time = self.events[self.current_event]
        cet = current_event_time
        current_event_time = time(cet.hour, cet.minute, cet.second)
        self.logger.debug( "current_event_time: {0}".format(current_event_time))
        fudge_factor = (datetime.combine(date(1,1,1), current_event_time) + timedelta(seconds=60)).time()
        self.logger.debug("fudge_factor: {0}".format(fudge_factor))
        status = current_event_time <= current_time <= fudge_factor

        if not status:
            return status

        return status

    def advance_counter(self):
        """
        Advance event counter to current event. Call this one time only from
        __init__().
        """
        current_time = self.current_time()
        fudge_factor = (datetime.combine(date(1,1,1), current_time) + timedelta(seconds=60)).time()
        if current_time > fudge_factor:
            # Leave self.current_event == 0. No counter advance.
            return

        for i in range(self.event_count):
            event = self.events[i]
            if event < current_time:
                self.current_event += 1
            else:
                break

    def loop(self):
        """
        Loop forever.
        """
        while True:
            is_event = self.is_event()
            self.logger.debug("is_event: {0}".format(is_event))
            if is_event:
                self.logger.debug("Initializing LMSCommandLineInterface.")
                sbcli = LMSCommandLineInterface()

                # LMSCommandLineInterface sets error on initialization failure.
                if sbcli.error:
                    self.logger.error(
                        "Unable to initialize LMSCommandLineInterface")
                else:
                    self.logger.debug(
                        "sending play command for event {0}".format(
                        self.current_event))
                    sbcli.play_chime()

                if self.current_event == self.event_count:
                    # Last event of the day, rewind.
                    self.current_event = 0
                else:
                    self.current_event += 1
            else:
                current_time_dt = datetime.combine(date(1,1,1),
                        self.current_time())
                next_event = self.events[self.current_event]
                next_event_dt = datetime.combine(date(1,1,1), next_event)
                diff = (next_event_dt - current_time_dt).total_seconds()

                self.logger.debug("diff: {0}".format(diff))
                self.logger.debug("current_event: {0}".format(self.current_event))
                self.logger.debug("event_count: {0}".format(self.event_count))

                if diff > 0:
                    sleep(diff)
                elif diff == 0:
                    # XXX: Prevent fast looping if diff == 0
                    sleep(1)
                elif diff < -10:
                    # Next event is tomorrow. diff is negative by the exact
                    # number of seconds between start time and now() which is
                    # very close to end time--i.e. now() ~ endtime. This is
                    # because we just completed the last chime of the day.
                    #
                    # Adding 86400 to the negative diff value will give us a
                    # sleep time that will correspond exactly with the next
                    # event which is the first event of tomorrow's active
                    # period. Ta Da!
                    sleep(diff + 86400)


if __name__ == '__main__':
    # TODO: Make this work standalone. Add logger and configparser.
    scheduler = ChimeScheduler()
    scheduler.daemon = False
    #scheduler.loop()
    scheduler.start()
    while True:
        sleep(5)
        print "scheduler is_alive:", scheduler.is_alive()

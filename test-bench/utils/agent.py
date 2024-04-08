from threading import Thread
from time import sleep


class Agent:
    def onStart(self) -> None:
        pass

    def doWork(self) -> int:
        pass

    def close(self) -> None:
        pass


class AgentRunner(Thread):
    def __init__(self, agentName: str, periodicitySec: int, agent: Agent):
        Thread.__init__(self, name=agentName)

        self.delegate = agent
        self.periodicitySec = periodicitySec

        self.started = False
        self.closed = False

    def run(self):
        if not self.started:
            self.delegate.onStart()
            self.started = True

        while not self.closed:
            workCount = self.delegate.doWork()
            if workCount and workCount > 0:
                continue

            sleep(self.periodicitySec)

    def close(self):
        self.closed = True
        self.delegate.close()

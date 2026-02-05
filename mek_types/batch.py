import c104
import random
import time
import typing
import asyncio
from multiprocessing import Process

class MEKBatch(c104.Batch):
    def __init__(self, station: c104.Station, cause:c104.Cot, batch_count: int, batch_type: c104.Type, start_address: int, delay_transmit = 0.01, report_ms = 0):
        super().__init__(cause=cause)
        self.station = station
        self.batch_count = batch_count
        self.start_address = start_address
        self.batch_type = batch_type
        self.log_point = None
        self.report_ms = report_ms
        self.delay_transmit = delay_transmit

        for i in range(batch_count):
            st_point = self.station.add_point(io_address=start_address + i, type=batch_type, report_ms=report_ms)
            st_point.value = float(random.randint(-63, 64))
            self.add_point(st_point)

    def update_batch(self):
        for point in self.points:
            point.value = float(random.randint(-63, 64))

    def set_values(self, values):
        for point, value in zip(self.points, values):
            point.value = float(value)

    def set_report_ms(self, report_ms):
        for point in self.points:
            point.report_ms = report_ms

    def add_receive_handler(self, handler):
        for point in self.points:
            point.on_receive(callable=handler)

    async def async_transmit(self, on_respond = False):
        self.transmit(on_respond)

    def transmit(self, on_respond = False):
        if on_respond:
            for point in self.points:
                res = point.transmit(self.cot)
                time.sleep(self.delay_transmit)
            if self.log_point is not None:
                self.log_point.transmit(self.cot)
        else:
            for point in self.points:
                res = point.transmit(self.cot)
            time.sleep(self.delay_transmit)
            if self.log_point is not None:
                self.log_point.transmit(self.cot)


    @classmethod
    def from_batch(cls, batch, station):
        return  cls(station, cause=batch.cot, batch_type=batch.type, start_address=batch.start_address, batch_count=batch.batch_count)


class StationsBatch:
    def __init__(self, batches: typing.List[MEKBatch] = None):
        self.mek_batches = [] if batches is None else batches

    def add_batch(self, batch: MEKBatch):
        self.mek_batches.append(batch)

    def set_report_ms(self, report_ms):
        for batch in self.mek_batches:
            batch.set_report_ms(report_ms)

    @property
    def batches(self):
        return self.mek_batches

    @batches.setter
    def batches(self, batches):
        self.mek_batches = batches

    @staticmethod
    async def __async_transmit(batch: MEKBatch, on_respond: bool):
        await batch.async_transmit(on_respond=on_respond)


    async def async_transmit(self, on_respond = False):
        tasks = [asyncio.create_task(self.__async_transmit(batch, on_respond)) for batch in self.mek_batches]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        # print(done)

    def multiprocess_transmit(self, on_respond = False):
        processes = [Process(batch.transmit(on_respond=on_respond)) for batch in self.mek_batches]
        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def transmit(self, on_respond = False):
        for batch in self.mek_batches:
            batch.transmit(on_respond=on_respond)

    def set_values(self, values):
        for batch in self.mek_batches:
            batch.set_values(values)

    def add_receive_handler(self, handler):
        for batch in self.mek_batches:
            batch.add_receive_handler(handler)



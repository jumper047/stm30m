# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot


import serial

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu


class Stm30Connection(QObject):

    newModbusEvent = pyqtSignal(str, str)
    stateUpdated = pyqtSignal(object)

    def connectToAnalyzer(self, port, baudrate, address):
        self.master = modbus_rtu.RtuMaster(
            serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        self.master.set_timeout(3.0)
        self.newModbusEvent.emit(u"COM порт инициализирован", "b")
        self.stmAddress = address

    @pyqtSlot()
    def getState(self):
        try:
            concentration = self.master.execute(
                self.stmAddress, cst.READ_HOLDING_REGISTERS, 0x0, 0x2, data_format=">BBBB")
            threshold1 = self.master.execute(
                self.stmAddress, cst.READ_HOLDING_REGISTERS, 0x2, 0x2, data_format=">BBBB")
            threshold2 = self.master.execute(
                self.stmAddress, cst.READ_HOLDING_REGISTERS, 0x4, 0x2, data_format=">BBBB")
            state = self.master.execute(
                self.stmAddress, cst.READ_HOLDING_REGISTERS, 0x23, 0x1, data_format=">BB")
        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")
            return None
        concentration = self._convertBcdToFloat(concentration)
        threshold1 = self._convertBcdToFloat(threshold1)
        threshold2 = self._convertBcdToFloat(threshold2)
        state = self._transcribeFlags(state)
        self.stateUpdated.emit([concentration, threshold1, threshold2, state])
        self.newModbusEvent.emit(u"Данные обновлены", "b")

    @pyqtSlot(float, int)
    def setThreshold1(self, threshold, bl_flag):
        message = [0, 3] + self._convertFloatToBcd(threshold)
        try:
            if self.master.execute(
                    self.stmAddress,
                    cst.WRITE_MULTIPLE_REGISTERS,
                    0x20, data_format=">BBBBBB",
                    output_value=message) == (0x20, 3):
                self.newModbusEvent.emit(u"Порог 1 успешно установлен", "g")
            else:
                self.newModbusEvent.emit(u"Ошибка установки порога", "r")
        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")

        message = [0, 0x13, 0, bl_flag]
        try:
            if self.master.execute(
                    self.stmAddress,
                    cst.WRITE_MULTIPLE_REGISTERS,
                    0x20, data_format=">BBBB",
                    output_value=message) == (0x20, 3):
                self.newModbusEvent.emit(u"Тип порога установлен", "g")
            else:
                self.newModbusEvent.emit(u"Ошибка установки типа порога", "r")

        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")

    @pyqtSlot(float, int)
    def setThreshold2(self, threshold, bl_flag):
        message = [0, 4] + self._convertFloatToBcd(threshold)
        try:
            if self.master.execute(
                    self.stmAddress,
                    cst.WRITE_MULTIPLE_REGISTERS,
                    0x20, data_format=">BBBBBB",
                    output_value=message) == (0x20, 3):
                self.newModbusEvent.emit(u"Порог 2 успешно установлен", "g")
            else:
                self.newModbusEvent.emit(u"Ошибка установки порога", "r")
        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")

        message = [0, 0x14, 0, bl_flag]
        try:
            if self.master.execute(
                    self.stmAddress,
                    cst.WRITE_MULTIPLE_REGISTERS,
                    0x20, data_format=">BBBB",
                    output_value=message) == (0x20, 3):
                self.newModbusEvent.emit(u"Тип порога установлен", "g")
            else:
                self.newModbusEvent.emit(u"Ошибка установки типа порога", "r")

        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")

    # Not implemented yet
    @pyqtSlot()
    def calibrateZero(self):
        pass

    @pyqtSlot()
    def calibrateEnd(self):
        pass

    @pyqtSlot(int)
    def setAddress(self, address):
        message = [0, 5] + self._convertFloatToBcd(address)
        try:
            if self.master.execute(
                    self.stmAddress,
                    cst.WRITE_MULTIPLE_REGISTERS,
                    0x20, data_format=">BBBBBB",
                    output_value=message) == (0x20, 3):
                self.newModbusEvent.emit(u"Адрес газоанализатора изменён", "g")
            else:
                self.newModbusEvent.emit(u"Ошибка установки адреса", "r")

        except modbus_tk.exceptions.ModbusInvalidResponseError:
            self.newModbusEvent.emit(u"Ошибка связи", "r")

    def _convertBcdToFloat(self, data):
        sign = 1 if data[0] < 128 else -1
        digit = 5 - (data[0] & 0xf)
        number = 0
        for byte in data[1:]:
                for nibble in [byte >> 4, byte & 0xf]:
                    number += nibble * (10 ** digit)
                    digit -= 1
        return float(number * sign)

    def _transcribeFlags(self, data):
        raw_state = data[1] & 0x7
        state = u"Обрыв" if data[1] & 4 else u"ОК"
        t1 = u"П1" if data[1] & 2 else ""
        t2 = u"П2" if data[1] & 1 else ""
        return " ".join([state, t1, t2])

    def _convertFloatToBcd(self, decimal):
        sign = 0 if decimal >= 0 else 1
        point = len(str(decimal).split(".")[1]) if decimal % 1 != 0 else 0
        decimal = int(decimal * (10 ** point))
        if len(str(decimal)) > 6:
            raise ValueError("Expected 6 or less digits in decimal, got {}"
                             .format(len(str(decimal))))
        bcd = []
        for i in range(3):
            rem = decimal % 100
            byte = ((rem // 10) << 4) + (rem % 10)
            bcd = [byte] + bcd
            decimal = decimal // 100
        return [(sign << 7) + point] + bcd

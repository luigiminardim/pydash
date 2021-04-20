from r2a.ir2a import IR2A
import math
from player.parser import *
import time
from statistics import mean
from base.whiteboard import Whiteboard


class R2A_Bola(IR2A):

    qualities = []

    paramNotRebuffer = 0.5  # (gama)

    paramBufferVsPerformance = 0.0  # (V)

    def __init__(self, id):
        IR2A.__init__(self, id)

    def utility(self, quality):  # (v_m)
        return math.log(quality / min(self.qualities))

    def phi(self, quality, bufferSize):
        return (self.paramBufferVsPerformance * self.utility(quality)
                + self.paramBufferVsPerformance * self.paramNotRebuffer * 1
                - bufferSize) / quality

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qualities = parsed_mpd.get_qi()
        maxQuality = self.qualities[len(self.qualities) - 1]
        self.paramBufferVsPerformance = (
            60 - 1) / (self.utility(maxQuality) + self.paramNotRebuffer)
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        msg.add_quality_id(self.qualities[0])
        selectedQuality = self.qualities[0]
        print("PLAYBACK BUFFER SIZE", len(Whiteboard.get_instance().get_playback_buffer_size()))
        print("BUFFER", Whiteboard.get_instance().get_buffer())
        bufferSize = len(Whiteboard.get_instance().get_buffer())
        maxPhi = -math.inf;
        print("BUFFER SIZE", bufferSize)
        for quality in self.qualities:
            currentPhi = self.phi(quality, bufferSize) 
            if currentPhi >= maxPhi:
                maxPhi = currentPhi
                selectedQuality = quality
        print("QUALITY", selectedQuality)
        msg.add_quality_id(selectedQuality)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass

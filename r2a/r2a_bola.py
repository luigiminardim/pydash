from r2a.ir2a import IR2A
import math
from player.parser import *
import time
from statistics import mean
from base.whiteboard import Whiteboard
from base.configuration_parser import ConfigurationParser


class R2A_Bola(IR2A):

    _qualities = []

    _smoothness_weight = 0.0  # (\gama)

    _performance_weight = 0.0  # (V)

    def __init__(self, id):
        IR2A.__init__(self, id)

    def _utility(self,  quality):
        return math.log(quality / min(self._qualities))

    def _trend_to_download(self, quality, buffer_size):
        return (
            self._performance_weight * self._utility(quality)
            + self._performance_weight * self._smoothness_weight
            - buffer_size
        ) / quality

    def _select_quality(self, buffer_size):
        selected_quality = None
        max_trend = -math.inf
        for quality in self._qualities:
            quality_trend = self._trend_to_download(quality, buffer_size)
            if quality_trend >= max_trend:
                selected_quality = quality
                max_trend = quality_trend
        return selected_quality

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self._qualities = parsed_mpd.get_qi()
        max_buffer_size = ConfigurationParser.get_instance().get_parameter('max_buffer_size')
        min_quality = self._qualities[0]
        snd_quality = self._qualities[1]
        max_quality = self._qualities[len(self._qualities) - 1]
        self._smoothness_weight = (
            (max_buffer_size - 1)
            * (self._utility(min_quality) * snd_quality - self._utility(snd_quality) * min_quality)
            - 2 * self._utility(max_quality) * (snd_quality - min_quality)
        ) / (
            (snd_quality - min_quality) * (2 - max_buffer_size)
        )
        self._performance_weight = (
            max_buffer_size - 1) / (self._utility(max_quality) + self._smoothness_weight)
        self.send_up(msg)
        print('Qualities: ', self._qualities)
        print('Min quality: ', min_quality)
        print('Second quality: ', snd_quality)
        print('Max quality: ', max_quality)
        print('Smoothness weight: ', self._smoothness_weight)
        print('Performance weight: ', self._performance_weight)

    def handle_segment_size_request(self, msg):
        buffer_size = Whiteboard.get_instance().get_amount_video_to_play()
        selected_quality = self._select_quality(buffer_size)
        msg.add_quality_id(selected_quality)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass

# Trabalho feito por:
# Luigi Minardi Ferreira Maia 17/0017141
# Gabriel Cunha Bessa Vieira 16/0120811

from r2a.ir2a import IR2A
import math
from player.parser import *
import time
from statistics import mean
from base.whiteboard import Whiteboard
from base.configuration_parser import ConfigurationParser


class R2A_Bola(IR2A):

    # S_m / p = S_m / 1 = S_m
    S = []

    g = 0.0  # \gamma

    V = 0.0

    def __init__(self, id):
        IR2A.__init__(self, id)

    def v(self,  m):
        '''
        Marginal utility
        v_m = ln(S_m / S_0)
        '''
        return math.log(self.S[m] / self.S[0])

    def t(self, m):
        '''
        Tendency
        t_m = (V * (v_m + \gamma * p) - Q) / (S_m)
        '''
        Q = Whiteboard.get_instance().get_amount_video_to_play()
        return (self.V * (self.v(m) + self.g * 1) - Q) / self.S[m]

    def _select_quality_index(self):
        '''
        m that maximizes t(m)
        '''
        m_selected = None
        t_max = -math.inf
        for m in range(0, len(self.S) - 1):
            t = self.t(m)
            if t >= t_max:
                m_selected = m
                t_max = t
        return m_selected

    def initialize(self):
        pass

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        '''
        V = (Q_max - 1) / (v_max + \gamma  * p)
        \gamma = ((Q_max - 1) * (v_0 * S_1 - v_1 * S_0) - 2 * v_max * (S_1 - S_0)) / (p * (S_1 - S_0) * (2 - (Q_max - 1)))
        '''
        parsed_mpd = parse_mpd(msg.get_payload())
        self.S = parsed_mpd.get_qi()
        Q_max = ConfigurationParser.get_instance().get_parameter('max_buffer_size')
        v_max = self.v(len(self.S) - 1)
        self.g = (
            (Q_max - 1) * (self.v(0) * self.S[1] - self.v(1) * self.S[0])
            - 2 * v_max * (self.S[1] - self.S[0])
        ) / (
            1 * (self.S[1] - self.S[0]) * (2 - Q_max - 1)
        )
        self.V = (Q_max - 1) / (v_max + self.g * 1)
        self.send_up(msg)
        print('Qualities: ', self.S)
        print('Smoothness weight: ', self.g)
        print('Performance weight: ', self.V)
        print('Q_max', Q_max)
        print('v_max', v_max)

    def handle_segment_size_request(self, msg):
        m = self._select_quality_index()
        msg.add_quality_id(self.S[m])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)

    def finalization(self):
        pass

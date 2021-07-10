# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ********************************************* Time ***************************************************************
import graph_scheduler

__all__ = [
    'TimeScale', 'Time', 'TimeHistoryTree'
]

# timescale mappings to pnl versions
_time_scale_mappings = {
    "TIME_STEP": graph_scheduler.time.TimeScale.CONSIDERATION_SET_EXECUTION,
    "TRIAL": graph_scheduler.time.TimeScale.ENVIRONMENT_STATE_UPDATE,
    "RUN": graph_scheduler.time.TimeScale.ENVIRONMENT_SEQUENCE,
}
for our_ts, scheduler_ts in _time_scale_mappings.items():
    graph_scheduler.set_time_scale_alias(our_ts, scheduler_ts)

TimeScale = graph_scheduler.TimeScale
Time = graph_scheduler.Time
TimeHistoryTree = graph_scheduler.TimeHistoryTree

_doc_subs = {
    'TimeScale': [
        (
            r'(a single\n *call to `run <Scheduler\.run>`)',
            '\\1 (a single input to a\n        `Composition <Composition>`.)'
        ),
        (
            r', managed by the\n *environment using the Scheduler.',
            r'. In PsyNeuLink, this is the scope of a call to the `run <Composition.run>` method of a `Composition <Composition>`, consisting of one or more `TRIALs <TimeScale.TRIAL>`.'
        ),
    ]
}

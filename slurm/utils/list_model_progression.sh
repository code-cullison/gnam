#!/bin/bash

\ls -tr ../logs/7_model_update.job.gpu00*.out | head -1 | xargs grep -A 1 -he 'initial models:' | grep -e 'min/max';
\ls -rt ../logs/7_model_update.job.gpu00*.out | xargs grep -A 1 -he 'new models:' | grep -e 'min/max';

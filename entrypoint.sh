#!/bin/bash --login

set +euo pipefail
conda activate emistream
set -euo pipefail

exec "$@"

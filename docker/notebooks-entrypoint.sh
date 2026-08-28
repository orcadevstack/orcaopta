#!/bin/bash

echo ""
echo "==============================================="
echo "   ORCAOPTA NOTEBOOKS — POWER-UP MODE"
echo "==============================================="
echo ""


jupyter labextension install @jupyterlab/toc --no-build
jupyter labextension install @ryantam626/jupyterlab_code_formatter --no-build
jupyter labextension install @jupyterlab/theme-dark-extension --no-build
jupyter lab build
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

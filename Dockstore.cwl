#!/usr/bin/env cwl-runner

class: CommandLineTool
id: "cnvToGenes"
label: "cnvToGenes workflow"
cwlVersion: v1.0
description: |
    A Docker container for the cnvToGenes workflow. See the [github repo](https://github.com/Jeltje/cnvtogenes) for more information.
    ```
    Usage:
    # fetch CWL
    $> dockstore cwl --entry quay.io/jeltje/cnvtogenes:v1.0.0 > Dockstore.cwl
    # make a runtime JSON template and edit it (or use the content of sample_configs.json in this git repo)
    $> dockstore convert cwl2json --cwl Dockstore.cwl > Dockstore.json
    # run it locally with the Dockstore CLI
    $> dockstore launch --entry quay.io/jeltje/cnvtogenes:v1.0.0 \
        --json Dockstore.json
    ```

dct:creator:
  "@id": "jeltje"
  foaf:name: Jeltje van Baren
  foaf:mbox: "mailto:jeltje.van.baren@gmail.com"

requirements:
  - class: DockerRequirement
    dockerPull: "quay.io/jeltje/cnvtogenes:v1.0.0"

hints:
  - class: ResourceRequirement
    coresMin: 1

inputs:

  - id: "#inputdir"
    type: Directory
    doc: "Directory with input cnv files"
    inputBinding:
      prefix: -c

  - id: "#annotation"
    type: File
    doc: "Genome annotation in BED format"
    format: "http://edamontology.org/format_3003"
    inputBinding:
      prefix: -g

  - id: "#chromflag"
    type: boolean
    inputBinding:
      prefix: -d

  - id: "#roundflag"
    type: boolean
    inputBinding:
      prefix: -r



stdout: genomefile

outputs: 
  - id: output
    type: stdout

baseCommand: []


# cnvtogenes

Program (and docker container instructions) for mapping CNV segment scores to a list of genes.

**Input** is an annotation in `.bed` format plus a directory that contains `*.cnv` files. This is the standard five column output for the Varscan CNV caller and consists of

```
sampleID    chrom    loc.start    loc.end    num.mark    seg.mean
```  
**Output** is a table with samples in columns and gene scores in rows. This file format is similar to [gistic](archive.broadinstitute.org/cancer/cga/gistic) allgenes output.

# The code

To map segment scores to genes, we need to make decisions about duplicated genes and genes that span multiple segments.

For duplicated gene IDs in the input file, the code selects the most extreme score from the sample. This means that the score for one sample may come from a different genome location that the score for another. If you don't want the program to do this, please make sure your gene IDs are unique.

When a gene overlaps multiple segments, again the most extreme score (positive or negative) is reported.

*Note: An earlier implementation of the code reported any such breakpoints but this does not fit in the gistic style format. If breakpoints are important to you, please [contact the author](mailto:jeltje.van.baren@gmail.com)*.

To run `cnvtogenes.py` you can dowload it from the github repo directly:
`wget https://raw.githubusercontent.com/jeltje/cnvtogenes/master/cnvToGenes.py`
cnvtogenes.py requires the intervaltree package, which you can retrieve using `pip install intervaltree`.

Alternatively you can run the code via a docker container. For the examples below, I am assuming this.

## Getting the docker container

The latest cnvtogenes docker image can be pulled directly from quay.io using
`docker pull quay.io/jeltje/cnvtogenes`

Alternatively, you can build from the github repo:
```
git clone https://github.com/jeltje/cnvtogenes.git
cd cnvtogenes
docker build -t jeltje/cnvtogenes .
```

## Running the docker container

For details on running docker containers in general, see the excellent tutorial at https://docs.docker.com/

To see a usage statement, run

``
docker run jeltje/cnvtogenes -h
``

### Example input:

``
docker run -v /path/to/input/files:/data jeltje/cnvtogenes --cnvdir <inputdir> --genefile <genome annotation.bed> > output.table 
``

where

`inputdir` is the directory that contains `.cnv` files. You can get these through [Varscan](https://github.com/Jeltje/varscan) or [ADTEx](https://github.com/Jeltje/adtex)

`genome annotation.bed` is a [bed format](https://genome.ucsc.edu/FAQ/FAQformat#format1) file containing your genes of interest. 

It is important that the chromosome annotation (`chr7` vs `7`) matches between the bed file and the .cnv files. If your bed file uses `chr` but your cnv files do not, you can set the `--nochr` flag.

### Output

The program writes to `STDOUT` so you can capture the results using the `>` sign.

If you want to do a test run, please `git clone https://github.com/jeltje/cnvtogenes.git` and look in the `test/` directory. Instructions are in the `test/README.md` file.

**Important note**: `cnvtogenes.py` does NOT apply any cutoffs to the scores.

#!/usr/bin/env python2.7

import sys, os, re, getopt
import glob
import argparse
from collections import OrderedDict
from intervaltree import Interval, IntervalTree

usage = sys.argv[0]+"""

Takes a gene file in bed format and a directory with .cnv outputs
Creates a table with log scores for all genes from all samples, 
in gistic style format (genes on rows, samples on columns)
When genes don't fully fall in one segment, take most extreme score

"""
def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cnvdir', required=True, help='Directory with cnv files')
    parser.add_argument('-g', '--genefile', required=True, help='input coordinate file (bed format)')
    parser.add_argument('-d', '--nochr', help="chromosomes in cnv files do not start with chr", action='store_true')
    parser.add_argument('-r', '--round', help="round scores to nearest integer", action='store_true')
    return parser

class geneSet(object):
    """Genes are separated by chromosome and stored by coordinate in an intervaltree"""
    def __init__(self, nochr):
        self.chromdict = dict()
        self.nochr = False
        if nochr:
            self.nochr = True
    def add(self, inline):
        global geneList
        global dupGenes
        cfields = inline.split("\t")
        chrom = cfields[0]
        if self.nochr:
            chrom = re.sub('^chr', '', chrom)
            if chrom == 'Y':
                chrom = '24'
            elif chrom == 'X':
                chrom = '23'
        start = int(cfields[1])
        end = int(cfields[2])
        # get a unique gene ID
        gid = cfields[3]
        if gid in geneList:
            if gid in dupGenes:
                ngid = "{}.{}".format(len(dupGenes[gid]), gid)
                dupGenes[gid].append(ngid)
            else:
                ngid = "0." + gid
                dupGenes[gid] = [ngid]
            gid = ngid
        if not chrom in self.chromdict:
            self.chromdict[chrom] = IntervalTree()
        coord = "{}\t{}:{}-{}".format(gid, chrom, start, end)
        self.chromdict[chrom][start:end] = coord
        # coord is two words so it gets interpreted as two variables in the main program
        return coord

class segment(object):
    def __init__(self, inline, doround):
        cfields = inline.split("\t")
        self.chrom = cfields[1]
        self.start = int(cfields[2])
        self.end = int(cfields[3])
        self.markers = int(cfields[4])
        self.score = float(cfields[5])
        if doround:
            self.score = int(round(self.score))

def bestScore(dupGenes, foundGenes):
    """Remove duplicates from foundGenes dict; keep most extreme score"""
    for dg in dupGenes:
        # it is possible that only subIDs were found in the sample so keep track with a flag
        found = False
        hscore = 0
        if dg in foundGenes:
            found = True
            hscore = foundGenes[dg]
        #The dupGenes dictionary links alternative IDs to the main gene ID
        for subID in dupGenes[dg]:
            if subID in foundGenes:
                found = True
                if abs(foundGenes[subID]) > abs(hscore):
                    hscore = foundGenes[subID]
                del foundGenes[subID]
        if found:
            foundGenes[dg] = hscore
    return foundGenes

def removeDups(dupGenes, geneList):
    """Get values for all keys in dupGenes and remove from geneList"""
    mset = set()
    for gid in dupGenes:
        # union operator
        mset |= set(dupGenes[gid])
    return list(set(geneList) - mset)

# Main
# Run program
parser = build_parser()
args = parser.parse_args()


# Read in segment list
# also create a dictionary of orderedDicts to hold results per sample
geneList = set()
dupGenes = dict()
geneDict = OrderedDict()
genes = geneSet(args.nochr)
with open(args.genefile, 'r') as l:
    for inline in l:
        gid, coord = genes.add(inline.strip()).split('\t')
        if gid in geneList:
            print "already have gid", gid, coord
        geneList.add(gid)
        # This dictionary will keep track of sample scores for the current gene
        geneDict[gid] = OrderedDict()

header = 'gene'
# now for every segment, find the genes that overlap
#https://pypi.python.org/pypi/intervaltree
for fname in glob.glob(os.path.join(args.cnvdir, '*.cnv')):
    with open(fname, 'r') as g: #, open(fname+'.list', 'w') as o:
        sample = os.path.basename(fname).split('.')[0]
        print >>sys.stderr, sample
        header += "\t{}".format(sample)
        foundGenes = dict()
        for inline in g:
            if inline.startswith('ID') or inline.startswith('Sample'):
               continue
            myseg = segment(inline.strip(), args.round)
            # must have at least 10 markers covering the segment
            if myseg.markers < 10:
                continue
            # for split genes, take most extreme score
            if not myseg.chrom in genes.chromdict:
                continue
            someOverlap = genes.chromdict[myseg.chrom].search(myseg.start, myseg.end)
            for i in someOverlap:
                gid = i[2].split('\t')[0]
                if gid in foundGenes:
                    #print >>sys.stderr, "found breakpoint in", gid, i[2], myseg.start, myseg.end, myseg.markers
                    #if abs(myseg.score) > abs(foundGenes[gid]):
                    if abs(myseg.score) > abs(foundGenes[gid]):
                       foundGenes[gid] = myseg.score
                else:
                    foundGenes[gid] = myseg.score
        foundGenes = bestScore(dupGenes, foundGenes)
        for gene in geneList:
            score = 'NA'
            if gene in foundGenes:
                score = foundGenes[gene]
            # should do something here
            geneDict[gene][sample] = str(score)

# Before printing, remove duplicate genes from the output
geneList = removeDups(dupGenes, geneList)
# samples have remained in the same order
print header
for gene in geneList:
    values = []
    for sample, score in geneDict[gene].items():
        values.append(score)
    print "{}\t{}".format(gene,"\t".join(s for s in values))



























#! /usr/bin/env python
""" 
Unit-test for run-tests, it just tests that the pipeline runs and produces correct results
"""

import unittest
import urllib
import os
import tempfile
import time
import multiprocessing
from subprocess import check_call
from stpipeline.core.pipeline import *

class TestPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Obtain paths and files.
        testdir = str(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
        self.infile_normal_fw = os.path.join(testdir, 'input/miseqF1/testdata_R1.fastq')
        self.infile_normal_rv = os.path.join(testdir, 'input/miseqF1/testdata_R2.fastq')
        self.infile_mc_fw = os.path.join(testdir, 'input/miseqF1/testdata_R1_MC.fastq')
        self.infile_mc_rv = os.path.join(testdir, 'input/miseqF1/testdata_R2_MC.fastq')
        self.annotfile = os.path.join(testdir, 'config/annotations/mouse_grcm38_chromosome19.gtf')
        self.chipfile = os.path.join(testdir, 'config/idfiles/130307_Design3_27mer.txt')
        self.expnameNormal = "mouse_normal_test"
        self.expnameMC = "mouse_mc_test"

        # Obtain temp dir
        self.tmpdir = tempfile.mkdtemp(prefix="st_pipeline_test_temp")
        print "ST Pipeline Test Temporary directory " + self.tmpdir
        self.outdir = tempfile.mkdtemp(prefix="st_pipeline_test_output")
        print "ST Pipeline Test Temporary output " + self.outdir
        self.error_file = os.path.join(self.tmpdir, 'error.log')
        self.logFile = tempfile.mktemp(prefix="st_pipeline_test_log")
        print "ST Pipeline Test Log file " + self.logFile

        # Create genome index dirs.
        self.genomedir = os.path.join(self.tmpdir, 'config/genomes/mouse_grcm38')
        os.makedirs(self.genomedir)
        self.contamdir = os.path.join(self.tmpdir, 'config/contaminant_genomes/R45S5_R5S1')
        os.makedirs(self.contamdir)

        # Download and unpack fasta files
        try:
            print "Downloading genome files..."
            genomefasta = os.path.join(self.genomedir, "mouse_grcm38_chromosome19.fasta")
            genomefastagz = os.path.join(self.genomedir, "mouse_grcm38_chromosome19.fasta.gz")
            urllib.urlretrieve ("ftp://ftp.ensembl.org/pub/release-78/fasta/mus_musculus/dna/Mus_musculus.GRCm38.dna_rm.chromosome.19.fa.gz", genomefastagz)
            check_call(['gunzip', genomefastagz])
            genomegtf = os.path.join(self.genomedir, "mouse_grcm38.gtf")
            genomegtfgz = os.path.join(self.genomedir, "mouse_grcm38.gtf.gz")
            urllib.urlretrieve ("http://ftp.ensembl.org/pub/current_gtf/mus_musculus/Mus_musculus.GRCm38.78.gtf.gz", genomegtfgz)
            check_call(['gunzip', genomegtfgz])
            contamfasta = os.path.join(testdir, "config/contaminant_genomes/R45S5_R5S1/Rn45s_Rn5s.fasta")
            print "...finished downloading!"
        except Exception as e:
        	print e
        	self.assertTrue(0, "Downloading genome files failed \n")

        # Make genome indexes
        try:
            print "Creating genome indexes..."
            check_call(["STAR", "--runMode", "genomeGenerate",
                    "--runThreadN", str(multiprocessing.cpu_count() - 1),
                    "--genomeDir", self.genomedir,
                    "--genomeFastaFiles", genomefasta,
                    "--sjdbGTFfile", genomegtf,
                    "--sjdbOverhang", "100"])
            check_call(["STAR", "--runMode", "genomeGenerate",
                    "--runThreadN", str(multiprocessing.cpu_count() - 1),
                    "--genomeDir", self.contamdir,
                    "--genomeFastaFiles", contamfasta])
            print "...finished creating indexes!"
        except Exception as e:
        	print e
        	self.assertTrue(0, "Creating genome indexes failed \n")


        # Verify existence of input files
        assert (os.path.exists(self.infile_normal_fw))
        assert (os.path.exists(self.infile_normal_rv))
        assert (os.path.exists(self.infile_mc_fw))
        assert (os.path.exists(self.infile_mc_rv))
        assert (os.path.isdir(self.genomedir))
        assert (os.path.isdir(self.contamdir))
        assert (os.path.exists(self.annotfile))
        assert (os.path.exists(self.chipfile))
        assert (os.path.isdir(self.outdir))
        assert (os.path.isdir(self.tmpdir))

        # create a pipeline Instance
        self.pipeline = Pipeline()

        # init pipeline arguments
        self.pipeline.allowed_missed = 6
        self.pipeline.allowed_kimera = 7
        self.pipeline.min_length_trimming = 28
        self.pipeline.trimming_rw_bowtie = 5
        self.pipeline.min_quality_trimming = 20
        self.pipeline.clean = False
        self.pipeline.s = 0
        self.pipeline.l = 27
        self.pipeline.e = 0
        self.pipeline.threads = 2
        self.pipeline.verbose = True
        self.pipeline.ids = os.path.abspath(self.chipfile)
        self.pipeline.ref_map = os.path.abspath(os.path.join(self.genomedir, "chromosome19"))
        self.pipeline.ref_annotation = os.path.abspath(self.annotfile)
        self.pipeline.htseq_mode = "intersection-nonempty"
        self.pipeline.htseq_no_ambiguous = False
        self.pipeline.contaminant_bt2_index = os.path.abspath(os.path.join(self.contamdir, "rnagenome"))
        self.pipeline.output_folder = os.path.abspath(self.outdir)
        self.pipeline.temp_folder = os.path.abspath(self.tmpdir)
        self.pipeline.logfile = self.logFile


    def test_star_run(self):
        """
        Tests st_pipeline on a mouse data subset with normal fastq files
        """
        # Add normal parameters
        self.pipeline.expName = self.expnameNormal
        self.pipeline.Fastq_fw = self.infile_normal_fw
        self.pipeline.Fastq_rv = self.infile_normal_rv
        self.pipeline.molecular_barcodes = False
        self.pipeline.trimming_fw_bowtie = 51
        self.pipeline.keep_discarded_files = True

        # Start the pipeline
        #try:
        #	self.pipeline.createLogger()
        #	self.pipeline.sanityCheck()
        #	self.pipeline.run()
        #except Exception as e:
        #	print e
        #	self.assertTrue(0, "Running Normal Test failed \n")


    #@classmethod
        #def tearDownClass(self):
        #outcnt = os.listdir(self.outdir)
        #tmpcnt = os.listdir(self.tmpdir)
        #for cnt in outcnt:
        #	os.remove(os.path.join(self.outdir, cnt))
        #for cnt in tmpcnt:
        #	os.remove(os.path.join(self.tmpdir, cnt))
        #os.removedirs(self.outdir)
        #os.removedirs(self.tmpdir)


if __name__ == '__main__':
    unittest.main()
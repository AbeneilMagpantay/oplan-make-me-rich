"""omr: kernel of the crypto trading research system (kernel v1, formula language).

Everything in this package is KERNEL: the research loop may not edit it. Strategies are .omr
programs that the kernel parses (omr.lang) and interprets (omr.interp); no strategy code is
executed. Changes happen only through a re-key (python -m omr.kernel_lock rekey), followed by a
calibration on the locked kernel and the seal (python -m omr.kernel_lock seal).
"""

KERNEL_VERSION = "1"

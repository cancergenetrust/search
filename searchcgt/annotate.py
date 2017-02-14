from pyensembl import EnsemblRelease
import re

GRCh37 = EnsemblRelease(75)
GRCh38 = EnsemblRelease(77)


def vcf2genes(vcf):
    """
    Return genes from vcf using pyensemble
    """
    # grep the reference name out of the vcf
    reference = [s.lower() for s in re.findall(r"reference=(.*)$", vcf,
                                               flags=re.IGNORECASE | re.MULTILINE)]

    if "grch37" in reference or "hg18" in reference:
        assembly = GRCh37
    elif "grch38" in reference or "hg19" in reference:
        assembly = GRCh38
    else:
        print("Unknown assembly reference: {}".format(reference))
        return []

    # grep the chromosome and locus of all mutations
    regions = set(re.findall(r"^(\d{1,2})\s+(\d+)\s", vcf, flags=re.MULTILINE))

    return set([g for r in regions for g in assembly.gene_names_at_locus(int(r[0]), int(r[1]))])

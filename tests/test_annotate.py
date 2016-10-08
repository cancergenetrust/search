import searchcgt.annotate as annotate


def test_vcf2genes():
    genes = annotate.vcf2genes(open("tests/variants.vcf").read())
    assert genes == set([u'RP11-506B6.6', u'LAMA4', u'POLD1'])

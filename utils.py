def combine_haplotype(haplotype_list):
    names = [h['name'] for h in haplotype_list]
    print(",".join(names))
    return ",".join(names)
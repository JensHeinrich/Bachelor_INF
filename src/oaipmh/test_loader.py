from xml_loader import OAIXMLLoader,get_records



loader_single = OAIXMLLoader(
    ["/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml",]
)
loader = OAIXMLLoader(
    ["/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml","/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml"]

)
loader1 = OAIXMLLoader(
    ["/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml","/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml"]

)

loader2 = OAIXMLLoader(
    ["/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml","/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml"]

)

from lxml import etree

with open("/home/jens/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/2022-07-13__oai_dc__000000002200.xml") as f:
    tree = etree.parse(f)


def gen_yield():
    for r in get_records(tree):
        yield (r, "TEST")

def gen_yield_from():
    yield from get_records(tree)

print(len([i for i in gen_yield()]))

print(len([i for i in gen_yield_from()]))

print(len([i for i in loader_single]))

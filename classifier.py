# -*- encoding: utf-8 -*-

"""
testing text classifications

"""

from textblob.classifiers import NaiveBayesClassifier

tests = [
    ("I usually drink 12 oz of it", 'volume'),
    ("This thing weighs around 12 ounces", 'mass'),
    ("it says 16oz on the bottle", 'volume'),
    ("Can't speak regarding men but my gf is short and a normal, healthy weight. She keeps me warm most of the time because she just seems to run warm. Don't need an extra 100 lbs of fat or more to keep people warm.", 'mass'),  # noqa
    ("I don't really want to. I was in that situation before, where I measured the product but forgot that I had to put it into a slightly bigger box. \n\nI'm waiting to see how it looks upon arrival. The shipping method he paid for is for a package between 2-5kg with dimensions 120x60x60 cm, while the game has dimensions of  23,8x8,1x29,7 cm and weighs 0,78kg (according to amazon).", 'mass'),  # noqa
    ("12 oz French press, hand mill and a repurposed keureg to heat the water.", 'volume'),
    ("You can get a full 24 case of 12 oz beers at Costco for that price. And good beer, too.", 'volume'),
    ("UK here, \u00a310 a g or \u00a3200 Oz.", 'mass'),
]


if __name__ == '__main__':
    with open('oz_trainset.json', 'r') as fp:
        cl = NaiveBayesClassifier(fp, format='json')

    cl.show_informative_features()
    print "Accuracy: {}".format(cl.accuracy(tests))

    for test, expected in tests:
        prob = cl.prob_classify(test)
        if not prob.max() == expected:
            print 'FAILED'
            print '****\n{:.40}\n****'.format(test)
            print 'max: {} @ {}'.format(prob.max(), prob.prob(prob.max()))

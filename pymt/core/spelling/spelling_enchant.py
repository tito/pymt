'''
Enchant Spelling: Implements spelling backend based on enchant.
'''


import enchant

from pymt.core.spelling import SpellingBase, NoSuchLangError


class SpellingEnchant(SpellingBase):
    '''
    Spelling backend based on the enchant library.
    '''
    def __init__(self, language=None):
        self._language = None
        super(SpellingEnchant, self).__init__(language)

    def register_language(self, language, langpath=None):
        raise NotImplementedError('Runtime addition of languages not supported ' + \
                                  'by enchant backend.')

    def select_language(self, language):
        try:
            self._language = enchant.Dict(language)
        except enchant.DictNotFoundError:
            raise NoSuchLangError('No language for "%s" provided by the enchant ' % (language, ) + \
                                  'backend')

    def list_languages(self):
        # Note: We do NOT return enchant.list_dicts because that also returns
        #       the enchant dict objects and not only the language identifiers.
        return enchant.list_languages()

    def check(self, word):
        self._assure_initialization()
        return self._language.check(word)

    def suggest(self, fragment):
        self._assure_initialization()
        suggestions = self._language.suggest(fragment)
        # Don't show suggestions that are invalid
        suggestions = [s for s in suggestions if self.check(s)]
        return suggestions


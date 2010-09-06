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
        if not word:
            return None
        return self._language.check(word)

    def suggest(self, fragment):
        suggestions = self._language.suggest(fragment)
        # Don't show suggestions that are invalid
        suggestions = [s.decode('utf-8') for s in suggestions if self.check(s)]
        return suggestions


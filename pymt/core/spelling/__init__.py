'''
Spelling: Provide abstracted access to a range of spellchecking backends.
          Also provides word suggestions. The API is inspired by enchant,
          but other backends can be added that implement the same API.
'''

__all__ = ('Spelling', 'SpellingBase', 'NoSuchLangError', )

from pymt.core import core_select_lib


class NoSuchLangError(Exception):
    '''
    Exception to be raised when a specific language could not be found.
    '''
    pass

class NoLanguageSelectedError(Exception):
    '''
    Exception to be raised when a language-using method is called but no
    language was selected prior to the call.
    '''
    pass


class SpellingBase(object):
    '''
    Base class for all spelling providers. Supports some abstract methods for
    checking words and getting suggestions.
    '''
    def __init__(self, language=None):
        '''
        If a `language` identifier (such as 'en_US') is provided and a matching
        language exists, it is selected. If an identifier is provided and no
        matching language exists, a NoSuchLangError exception is raised by
        self.select_language().
        If no `language` identifier is provided, we just fall back to the first
        one that is available.
        '''
        langs = self.list_languages()
        try:
            # If no language was specified, we just use the first one
            # that is available.
            fallback_lang = langs[0]
        except IndexError:
            raise NoLanguageSelectedError("No languages available!")
        self.select_language(language or fallback_lang)

    def select_language(self, language):
        '''
        From the set of registered languages, select the first language
        for `language`.
        '''
        raise NotImplementedError('select_language() method not implemented ' + \
                                  'by abstract spelling base class!')

    def list_languages(self):
        '''
        Return a list of all languages supported by the registered languages.
        E.g.: ['en', 'en_GB', 'en_US', 'de', ...]
        '''
        raise NotImplementedError('list_languages() method not implemented ' + \
                                  'by abstract spelling base class!')

    def check(self, word):
        # XXX `word` is a string.
        '''
        If `word` is a valid word in `self._language`, return True.
        '''
        raise NotImplementedError('check() method not implemented by abstract ' + \
                                  'spelling base class!')

    def suggest(self, fragment):
        '''
        For a given `fragment` (i.e., part of a word or a word by itself),
        provide corrections (`fragment` may be misspelled) or completions
        as a list of strings.
        '''
        raise NotImplementedError('suggest() method not implemented by abstract ' + \
                                  'spelling base class!')


Spelling = core_select_lib('spelling', (
    ('enchant', 'spelling_enchant', 'SpellingEnchant'),
    ('osxappkit', 'spelling_osxappkit', 'SpellingOSXAppKit'),
))


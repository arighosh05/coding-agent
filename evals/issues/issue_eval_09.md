### code

```
class Solution(object):
    def isMatch(self, text: str, pattern: str) -> bool:
        if not pattern:
            return not text

        first_match = bool(text) and pattern[0] in {text[0], "."}

        if len(pattern) >= 2 and pattern[1] == "*":
            return (
                self.isMatch(text, pattern[2:])
                or first_match
                and self.isMatch(text[1:], pattern)
            )
        else:
            return first_match and self.isMatch(text[1:], pattern[1:])
```

### context

```
Given an input string s and a pattern p, the code implements regular expression matching with support for '.' and '*' where:
'.' Matches any single character.​​​​
'*' Matches zero or more of the preceding element.
The matching covers the entire input string (not partial).
```

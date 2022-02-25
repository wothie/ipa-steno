#!/usr/bin/env racket
#lang rash

(require racket/string)
(require racket/dict)
(require racket/list)

(define file-deps '(("combine_ipa.py") ;; that's here twice, because of circular dependency
                    ("eng_to_ipa_dict.py")
                    ("count.py" "combine_ipa.py")
                    ("counted_english.py" "affix_rules.py")
                    ("to_stems.py")
                    ("vowels_and_consonants.py" "eng_stems_to_ipa_dict.py")
                    ("simplify_ipa.py")
                    ("eng_to_simp_ipa_dict.py")
                    ("to_notation.py")
                    ("eng_to_notation_dict.py")
                    ("finalize_dict.py")
                    ("notation_to_eng_dict.py")))

;; fill the dictionary with the file hashes
(define file-to-hash
  (foldl (lambda (line hash)
                 ;; .last_version.txt has format "<hash> <filename>\n<hash> <filename>..."
                 (let ([line-list (string-split line)])
                      (dict-set hash
                        ;; filename
                        (cadr line-list)
                        ;; hash
                        (car line-list))))
         #hash()
         (string-split #{cat .last_version.txt} "\n")))

;; the tail from file-deps which needs to be recomputed due to changes
(define todo-list
  ;; drop all levels where the file hashes aren't what was saved in .last_version.txt
  (dropf file-deps
    (lambda (level) (andmap
            (lambda (filename) (string=?
                    (dict-ref file-to-hash filename)
                    (car (string-split #{md5sum $filename} " "))))
            level))))

;; recompute the rest
(for-each (lambda (filename)
  (begin
    (display (string-append "running " filename "\n")))
    #{python $filename})
  (flatten todo-list))

;; renew hashes in .last_version.txt
(define out-string (string-join
  (dict-map file-to-hash (lambda (filename hash)
    (string-append hash " " filename)))
  "\n"))
echo $out-string &>! .last_version.txt

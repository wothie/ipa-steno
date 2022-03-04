#!/usr/bin/env racket
#lang rash

(require racket/string)
(require racket/dict)
(require racket/list)

(define file-deps '(("eng_to_ipa_dict.py")
                    ("affix_rules.py")
                    ("to_stems.py")
                    ("vowels_and_consonants.py" "eng_composition.py")
                    ("count.py")
                    ("counts.py")
                    ("simplify_ipa.py")
                    ("eng_to_simp_ipa_dict.py")
                    ("to_notation.py")
                    ("eng_to_notation_dict.py")
                    ("finalize_dict.py")
                    ("notation_to_eng_dict.py")
                    ("keymap.py")
                    ("keys_to_eng_dict.py")))

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
                    (if (dict-has-key? file-to-hash filename)
                        (dict-ref file-to-hash filename)
                        'this is hopefully not a valid hash')
                    (car (string-split #{md5sum $filename} " "))))
            level))))

;; function to return from the script when a file fails
(define (end-on-fail command)
  (when (not
            (pipeline-success?
              (run-mixed-pipeline
                (unix-pipeline-member-spec command) #:return-pipeline-object #t)))
        (begin
          (display "Failure")
          (newline)
          (exit))))

;; recompute the rest
(for-each (lambda (filename)
  (begin
    (display (string-append "running " filename "\n"))
    ;; stop if one of the files failed. Assumes that successful execution causes no output.
    (end-on-fail `(python ,filename))))
  (flatten todo-list))

;; renew hashes in .last_version.txt
(define out-string (string-join
  (map (lambda (filename)
         (let ([line-list (string-split #{md5sum $filename})])
           (string-append (car line-list) " " filename)))
       (dict-keys file-to-hash))
  "\n"))
echo $out-string &>! .last_version.txt
echo Done

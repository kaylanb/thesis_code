(require 'package) ;; You might already have this line
  (add-to-list 'load-path "~/.emacs.d/lisp/")
  ;;(load "github-modern-theme") 
  (load "github-theme") 
  (add-to-list 'package-archives
	       '("melpa-stable" . "https://stable.melpa.org/packages/"))
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "http://elpa.gnu.org/packages/")))
(package-initialize) ;; You might already have this line

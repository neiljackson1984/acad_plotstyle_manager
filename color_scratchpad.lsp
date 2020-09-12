(defun LM:ACI->RGB ( c / o r )
    (if (setq o (vla-getinterfaceobject (vlax-get-acad-object) (strcat "autocad.accmcolor." (substr (getvar 'acadver) 1 2))))
        (progn
            (setq r
                (vl-catch-all-apply
                   '(lambda ( )
                        (vla-put-colorindex o c)
                        (list (vla-get-red o) (vla-get-green o) (vla-get-blue o))
                    )
                )
            )
            (vlax-release-object o)
            (if (vl-catch-all-error-p r)
                (prompt (strcat "\nError: " (vl-catch-all-error-message r)))
                r
            )
        )
    )
)

(setq i 0)

(setq aciColors (list))

(while (< i 256)
  (setq aciColors
    (append
      aciColors
      (list (LM:ACI->RGB i))
    )
  )
  (setq i (+ 1 i))
)

(setq message  "")

(setq i 0)
(while (< i (length aciColors) )
  (setq message
    (strcat message
      (itoa i) ": "
      "("
        (itoa (nth 0 (nth i aciColors))) ", "      
        (itoa (nth 1 (nth i aciColors))) ", "      
        (itoa (nth 2 (nth i aciColors)))  
      ")" "," "\n"
    )
  )
  (setq i (+ 1 i))
)

(princ message)(princ)

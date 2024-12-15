
(cl:in-package :asdf)

(defsystem "utils-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "IMU" :depends-on ("_package_IMU"))
    (:file "_package_IMU" :depends-on ("_package"))
    (:file "localisation" :depends-on ("_package_localisation"))
    (:file "_package_localisation" :depends-on ("_package"))
  ))
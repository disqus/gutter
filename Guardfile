guard :shell do
    watch(/^(tests|chimera)(.*)\.py$/) do |match|
        puts `python setup.py nosetests`
    end
end
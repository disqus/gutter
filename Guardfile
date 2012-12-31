guard :shell do
    watch(/^(tests|gutter)(.*)\.py$/) do |match|
        puts `python setup.py nosetests`
    end
end
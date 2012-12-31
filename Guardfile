guard :shell do
    watch(/^(tests|gutter)(.*)\.py$/) do |match|
        puts `env PYTHONHASHSEED=52753 python setup.py nosetests`
    end
end
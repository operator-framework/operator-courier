from subprocess import check_call


def before_tag(context, tag):
    if tag == 'cli':
        commands = [
            'make release',
            'pip install dist/operator_courier-*-none-any.whl',
            'operator-courier -v',
        ]

        for command in commands:
            exit_code = check_call(command, shell=True)
            assert exit_code == 0


def after_tag(context, tag):
    if tag == 'cli':
        cmd = 'make clean'
        exit_code = check_call(cmd, shell=True)
        assert exit_code == 0

from command.build import BuildCmd
from command.push import PushCmd
from command.validate import ValidateCmd

def all_commands():
    return {
        BuildCmd.name: BuildCmd,
        PushCmd.name: PushCmd,
        ValidateCmd.name: ValidateCmd,
    }

def main():
    BuildCmd().build()
    ValidateCmd().validate()

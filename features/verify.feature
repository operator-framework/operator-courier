@cli @verify
Feature: Operator Courier command line verify operation

  @valid
  Scenario Outline: Operator Courier should be able to verify the valid input yaml files
    * operator-courier should be able to verify the VALID input yaml files in the input directory "<source_dir>"

    Examples:
      |source_dir|
      |features/steps/yamls_for_bundle/valid_yamls_without_crds|
      |features/steps/yamls_for_bundle/valid_yamls_with_single_crd|
      |features/steps/yamls_for_bundle/valid_yamls_with_multiple_crds|

  @invalid
  Scenario Outline: Operator Courier should be able to verify the valid input yaml files
    * operator-courier should verify that the input yaml files in the input directory "<source_dir>" is invalid, return a non-zero status, and log error messages that contain "<error_message>"

    Examples:
      |source_dir                                                    |error_message|
      |features/steps/yamls_for_bundle/invalid_yamls_without_package |ERROR:operatorcourier.validate:Bundle does not contain any packages.|

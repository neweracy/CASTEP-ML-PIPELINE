#!perl
use strict;
use Getopt::Long;
use MaterialsScript qw(:all);

# List of alloy filenames in your STRUCTURES folder
my @alloys = (
    "Ti15Al1.xsd",
    "Ti14Al2.xsd",
    "Ti12Al4.xsd",
    "Ti8Al8.xsd",
    "Ti4Al12.xsd"
);

print "Starting CASTEP Batch Automation...\n";

foreach my $file (@alloys) {
    # Access the document via its project folder path
    my $docPath = "STRUCTURES/" . $file;
    my $system = $Documents{$docPath};

    if (!defined $system) {
        print "Warning: Could not find $docPath. Skipping...\n";
        next;
    }

    print "Running Geometry Optimization for: $file\n";

    my $results = Modules->CASTEP->GeometryOptimization->Run($system, Settings(
        EnergyCutoffQuality => 'Ultra-fine',
        EnergyCutoff => 420,
        CalculateStress => 'Yes',
        CellOptimization => 'Full',
        CalculateBondOrder => 'Mulliken',
        CalculateCharge => 'Mulliken',
        SpinPolarized => 'No'
    ));

    print "Successfully finished: $file\n";
}

print "All batch calculations completed successfully!\n";
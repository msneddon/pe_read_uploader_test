/*
A KBase module to wrap the MegaHit package.
*/

module PEReadUploaderTest {

	
	typedef structure {
		string workspace_name;
		string read_library_name;
		string output_contigset_name;

		string megahit_parameter_preset;

		int min_count;
		int k_min;
		int k_max;
		int k_step;
		list <int> k_list;
		int min_contig_len;
	} MegaHitParams;


	typedef structure {
		string report_name;
        string report_ref;
	} MegaHitOutput;

	funcdef run_megahit(MegaHitParams params) returns (MegaHitOutput output)
		authentication required;

};
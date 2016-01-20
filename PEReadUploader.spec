/*
A KBase module to wrap the MegaHit package.
*/

module PEReadUploaderTest {

	
	typedef structure {
	} Params;


	typedef structure {
		string report_name;
        string report_ref;
	} Output;

	funcdef upload(Params params) returns (Output output)
		authentication required;

};
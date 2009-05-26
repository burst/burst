#ifndef __BURST_UTIL_H__
#define __BURST_UTIL_H__

#include <vector>
#include <string>
#include <fstream>
#include <ctime>

void readVariablesFile(const char* file_name, std::vector<std::string>& out)
{
    // read the variable names we will be writing to a csv file
    ifstream varfile (file_name);

    if (!varfile.is_open ()) {
        std::cout <<
            "burstutil: ERROR: cannot find the variable files - no recording done. where is "
            << file_name << "?" << std::endl;
        return;
    }

    out.resize(0, "");

    while (!varfile.eof ()) {
        std::string line;
        getline (varfile, line);
        if (line.size () <= 0) {
            continue;
        }
        out.push_back (line);    // TODO - algorithms, copy?
    }
    varfile.close ();
}

std::string get_date ()
{
    time_t t = time (0);
    struct tm *lt = localtime (&t);
    char time_str[15];
    sprintf (time_str, "%04d%02d%02d_%02d%02d%02d", lt->tm_year + 1900,
             lt->tm_mon + 1, lt->tm_mday, lt->tm_hour, lt->tm_min,
             lt->tm_sec);
    return std::string (time_str);
}

#endif // __BURST_UTIL_H__


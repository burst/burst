#ifndef __RECORDING_THREAD_H__
#define __RECORDING_THREAD_H__

#include <string>

class RecordingThread {
private:
    std::string m_filename;
public:
    RecordingThread(std::string filename) : m_filename(filename) {
    };
    void run();
    bool m_continue; // write from outside to close thread (and file)
};

#endif // __RECORDING_THREAD_H__


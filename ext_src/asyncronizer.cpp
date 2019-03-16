#include <functional>
#include <memory>
#include <thread>
#include <sstream>
#include <iomanip>

#ifndef WITH_THREADS
    // Required for correct Python thread initialization in pybind11
    #define WITH_THREADS 1
#endif  // WITH_THREADS

#include <boost/asio.hpp>
#include <boost/system/error_code.hpp>

#include <pybind11/pybind11.h>

#include <dkuk/asyncronizer/asyncronizer.hpp>


namespace py = pybind11;
using namespace py::literals;


PYBIND11_MODULE(_asyncronizer_ext, module)
{
    module.doc() = "dkuk::asyncronizer C++ internals: Python asyncio <-> C++ Boost.Asio bridge";

    dkuk::asyncronizer::shared_ptr_managed_class<std::thread>{module, "Thread"}
        .def("join", &std::thread::join)
        .def("detach", &std::thread::detach)
        .def("joinable", &std::thread::joinable);

    dkuk::asyncronizer::shared_ptr_managed_class<
        boost::asio::executor_work_guard<boost::asio::io_context::executor_type>
    >{
        module,
        "IoContextWorkGuard"
    }
        .def_property_readonly(
            "owns_work",
            &boost::asio::executor_work_guard<boost::asio::io_context::executor_type>::owns_work
        )
        .def(
            "reset",
            &boost::asio::executor_work_guard<boost::asio::io_context::executor_type>::reset
        );

    dkuk::asyncronizer::shared_ptr_managed_class<boost::asio::io_context>{module, "IoContext"}
        .def(py::init())
        .def(py::init<int>())
        .def_property_readonly("stopped", &boost::asio::io_context::stopped)
        .def("stop", &boost::asio::io_context::stop)
        .def(
            "create_work_guard",
            [](std::shared_ptr<boost::asio::io_context> self_ptr)
                -> std::shared_ptr<boost::asio::executor_work_guard<boost::asio::io_context::executor_type>>
            {
                return std::make_shared<boost::asio::executor_work_guard<boost::asio::io_context::executor_type>>(
                    boost::asio::make_work_guard(*self_ptr)
                );
            }
        )
        .def(
            "start_runner",
            [](std::shared_ptr<boost::asio::io_context> self_ptr) -> std::shared_ptr<std::thread>
            {
                return std::make_shared<std::thread>(
                    [self_ptr = std::move(self_ptr)]() -> void
                    {
                        self_ptr->run();
                    }
                );
            }
        );

    py::class_<boost::system::error_category>{module, "ErrorCategory"}
        .def_property_readonly(
            "name",
            [](const boost::system::error_category &self) -> std::string
            {
                return self.name();
            }
        )
        .def(
            "__repr__",
            [](const boost::system::error_category &self) -> std::string
            {
                std::stringstream ss;
                ss << "ErrorCategory(name=" << std::quoted(self.name()) << ')';
                return ss.str();
            }
        );

    py::class_<boost::system::error_code>{module, "ErrorCode"}
        .def(py::init())
        .def(py::init<int, const boost::system::error_category &>(), "value"_a, "category"_a)
        .def("assign", &boost::system::error_code::assign, "value"_a, "category"_a)
        .def("clear", &boost::system::error_code::clear)
        .def_property_readonly("value", &boost::system::error_code::value)
        .def_property_readonly("category", &boost::system::error_code::category)
        .def_property_readonly(
            "message",
            [](const boost::system::error_code &self) -> std::string
            {
                return self.message();
            }
        )
        .def_property_readonly(
            "failed",
            [](const boost::system::error_code &self) -> bool
            {
                return bool(self);
            }
        )
        .def(
            "__eq__",
            [](const boost::system::error_code &self, const boost::system::error_code &other) -> bool
            {
                return (self == other)? true: false;
            }
        )
        .def(
            "__lt__",
            [](const boost::system::error_code &self, const boost::system::error_code &other) -> bool
            {
                return (self < other)? true: false;
            }
        )
        .def(
            "__repr__",
            [](const boost::system::error_code &self) -> std::string
            {
                std::stringstream ss;
                ss
                    << "ErrorCode(value=" << self.value()
                    << ", category=ErrorCategory(name=" << std::quoted(self.category().name())
                    << "), message=" << std::quoted(self.message()) << ')';
                return ss.str();
            }
        );
}

#include <chrono>
#include <functional>
#include <tuple>

#include <boost/asio/system_timer.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>

#include <dkuk/asyncronizer/asyncronizer.hpp>


namespace py = pybind11;
using namespace py::literals;


PYBIND11_MODULE(test_async_sleep_ext, module)
{
    module.doc() = "test_async_sleep_ext module";

    dkuk::asyncronizer::shared_ptr_managed_class<boost::asio::system_timer>{module, "SystemTimer"}
        .def(
            py::init(
                [](std::shared_ptr<boost::asio::io_context> io_context_ptr, double seconds)
                    -> std::shared_ptr<boost::asio::system_timer>
                {
                    auto p =
                        std::make_shared<
                            std::tuple<
                                std::shared_ptr<boost::asio::io_context>,
                                boost::asio::system_timer
                            >
                        >(
                            io_context_ptr,
                            boost::asio::system_timer{
                                *io_context_ptr,
                                std::chrono::duration_cast<std::chrono::seconds>(
                                    std::chrono::duration<double>(seconds)
                                )
                            }
                        );

                    return std::shared_ptr<boost::asio::system_timer>{p, &std::get<1>(*p)};
                }
            ),
            "io_context"_a,
            "seconds"_a
        )
        .def(
            "async_wait",
            [](
                std::shared_ptr<boost::asio::system_timer> self_ptr,
                std::function<void (boost::system::error_code ec)> on_ready
            ) -> void
            {
                self_ptr->async_wait(
                    [self_ptr, on_ready](const boost::system::error_code &ec)
                    {
                        on_ready(ec);
                    }
                );
            },
            "on_ready"_a
        );
}

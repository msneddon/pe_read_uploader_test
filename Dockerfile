FROM kbase/kbase:sdkbase.latest
MAINTAINER Michael Sneddon
# -----------------------------------------


WORKDIR /kb/module

# copy local wrapper files, and build
COPY ./ /kb/module
RUN mkdir -p /kb/module/work

RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]

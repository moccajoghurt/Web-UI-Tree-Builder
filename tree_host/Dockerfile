FROM python:alpine@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff

# Install system dependencies required for WeasyPrint
RUN apk update && apk add --no-cache \
    curl \
    glib-dev \
    gobject-introspection-dev \
    cairo-dev \
    pango-dev \
    gdk-pixbuf-dev \
    libffi-dev \
    fontconfig \
    ttf-dejavu \
    && rm -rf /var/cache/apk/*

# Update font cache
RUN fc-cache -f

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src

WORKDIR /src

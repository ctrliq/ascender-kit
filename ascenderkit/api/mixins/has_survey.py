from typing import Any, Callable

from ascenderkit.utils import random_title


class HasSurvey(object):
    # Supplied by the Page this is mixed into: response-body fields arrive
    # through Page.__getattr__, the rest are Page's own. Annotations rather
    # than assignments, so nothing is created at runtime.
    related: Any
    survey_enabled: bool
    patch: Callable[..., Any]

    def add_survey(self, spec=None, name=None, description=None, required=False, enabled=True):
        payload = dict(
            name=name or 'Survey - {}'.format(random_title()),
            description=description or random_title(10),
            spec=spec or [dict(required=required, question_name="What's the password?", variable="secret", type="password", default="foo")],
        )
        if enabled != self.survey_enabled:
            self.patch(survey_enabled=enabled)
        return self.related.survey_spec.post(payload).get()
